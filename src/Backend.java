import javax.jms.*;
import javax.naming.*;
import java.util.Properties;

public class Backend implements MessageListener {

    private TopicSession pubSession;
    private TopicSession subSession;
    private TopicPublisher publisher;
    private TopicConnection connection;
    private String username;


    public Backend(String topicName, String username, String password) {
        // Obtain a JNDI connection
        Properties env = new Properties();
        // Specify the JNDI properties specific to the vendor
        try {
            InitialContext jndi = new InitialContext(env);
            // Look up a JMS connection factory
            TopicConnectionFactory topicConnectionFactory = (TopicConnectionFactory)
                    jndi.lookup("TopicConnectionFactory");

            // Create a JMS Connection
            TopicConnection connection =
                    topicConnectionFactory.createTopicConnection();

            // Create two JMS session objects
            TopicSession pubSession =
                    connection.createTopicSession(false,
                            Session.AUTO_ACKNOWLEDGE);
            TopicSession subSession =
                    connection.createTopicSession(false,
                            Session.AUTO_ACKNOWLEDGE);

            // Look up a JMS topic
            Topic messageTopic = (Topic) jndi.lookup(topicName);

            TopicPublisher publisher =
                    pubSession.createPublisher(messageTopic);
            TopicSubscriber subscriber =
                    subSession.createSubscriber(messageTopic);

            // Set a JMS message listener
            subscriber.setMessageListener(this);

            // Intialize the Chat application
            set(connection, pubSession, subSession, publisher, username);

            // Start the JMS connection; allows messages to be delivered
            connection.start();


        } catch (NamingException e) {
            e.printStackTrace();
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }

    /* Initialize the instance variables */
    public void set(TopicConnection con, TopicSession pubSess,
                    TopicSession subSess, TopicPublisher pub,
                    String username) {
        this.connection = con;
        this.pubSession = pubSess;
        this.subSession = subSess;
        this.publisher = pub;
        this.username = username;
    }

    /* Close the JMS connection */
    public void close() throws JMSException {
        connection.close();
    }

    public static void main(String[] args) {
    }

    @Override
    public void onMessage(Message message) {

    }
}