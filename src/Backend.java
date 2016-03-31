import javax.jms.*;
import javax.naming.InitialContext;
import javax.naming.NamingException;

public class Backend  {

    static CountDown done = new CountDown(1);
    TopicConnection conn = null;
    TopicSession session = null;
    Topic topic = null;

    public static class ExListener implements MessageListener
    {
        public void onMessage(Message msg)
        {
            done.release();
            TextMessage tm = (TextMessage) msg;
            try {
                System.out.println("onMessage, recv text=" + tm.getText());
            } catch(Throwable t) {
                t.printStackTrace();
            }
        }
    }

    public void setupPubSub(){
        InitialContext iniCtx = null;
        try {
            iniCtx = new InitialContext();
            Object tmp = iniCtx.lookup("ConnectionFactory");
            TopicConnectionFactory tcf = (TopicConnectionFactory) tmp;
            conn = tcf.createTopicConnection();
            topic = (Topic) iniCtx.lookup("topic/testTopic");
            session = conn.createTopicSession(false,
                    TopicSession.AUTO_ACKNOWLEDGE);
            conn.start();
        } catch (NamingException e) {
            e.printStackTrace();
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }

    public void sendRecvAsync(String text){
        System.out.println("Begin sendRecvAsync");
        // Setup the PubSub connection, session
        setupPubSub();
        // Set the async listener

        TopicSubscriber recv = null;
        try {
            recv = session.createSubscriber(topic);
            recv.setMessageListener(new ExListener());
            // Send a text msg
            TopicPublisher send = session.createPublisher(topic);
            TextMessage tm = session.createTextMessage(text);
            send.publish(tm);
            System.out.println("sendRecvAsync, sent text=" + tm.getText());
            send.close();
            System.out.println("End sendRecvAsync");
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }

    public void stop() {
        try {
            conn.stop();
            session.close();
            conn.close();
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }

    public static void main(String args[]) {
        System.out.println("Begin TopicSendRecvClient, now=" +
                System.currentTimeMillis());
        Backend client = new Backend();
        client.sendRecvAsync("A text msg, now="+System.currentTimeMillis());
        try {
            client.done.acquire();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        client.stop();
        System.out.println("End TopicSendRecvClient");
        System.exit(0);
    }
}