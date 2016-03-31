import javax.jms.*;
import javax.naming.InitialContext;
import javax.naming.NamingException;

public class Subscriber {
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

    public void recvSync() {
        System.out.println("Begin recvSync");
        // Setup the pub/sub connection, session
        setupPubSub();

        // Wait upto 5 seconds for the message
        TopicSubscriber recv = null;
        try {
            recv = session.createSubscriber(topic);
            Message msg = recv.receive(5000);
            if (msg == null) {
                System.out.println("Timed out waiting for msg");
            } else {
                System.out.println("TopicSubscriber.recv, msgt="+msg);
            }
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
        System.out.println("Begin TopicRecvClient, now=" +
                System.currentTimeMillis());
        Subscriber client = new Subscriber();
        client.recvSync();
        client.stop();
        System.out.println("End TopicRecvClient");
        System.exit(0);
    }
}
