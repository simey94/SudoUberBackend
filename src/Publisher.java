import javax.jms.*;
import javax.naming.InitialContext;
import javax.naming.NamingException;

public class Publisher {

    TopicConnection conn = null;
    TopicSession session = null;
    Topic topic = null;

    public void setupPubSub() {
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

    public void sendAsync(String text) {
        System.out.println("Begin sendAsync");
        // Setup the pub/sub connection, session
        setupPubSub();
        // Send a text msg
        TopicPublisher send = null;
        try {
            send = session.createPublisher(topic);
            TextMessage tm = session.createTextMessage(text);
            send.publish(tm);
            System.out.println("sendAsync, sent text=" +  tm.getText());
            send.close();
            System.out.println("End sendAsync");
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
        System.out.println("Begin TopicSendClient, now=" +
                System.currentTimeMillis());
        Publisher client = new Publisher();
        client.sendAsync("A text msg, now="+System.currentTimeMillis());
        client.stop();
        System.out.println("End TopicSendClient");
        System.exit(0);
    }



}
