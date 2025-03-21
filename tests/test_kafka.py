from unittest.mock import patch, MagicMock
import unittest
from confluent_kafka import Producer

class TestKafkaProducer(unittest.TestCase):
    @patch("confluent_kafka.Producer")
    def test_produce(self, mock_producer):
        mock_instance = mock_producer.return_value
        mock_instance.produce.return_value = None  # Simulating successful send

        producer = Producer({"bootstrap.servers": "localhost:9092"})
        producer.produce("test-topic", key="key", value="message")

        mock_instance.produce.assert_called_with("test-topic", key="key", value="message")





from unittest.mock import patch, MagicMock
import unittest
from confluent_kafka import Consumer

class TestKafkaConsumer(unittest.TestCase):
    @patch("confluent_kafka.Consumer")
    def test_consume(self, mock_consumer):
        mock_instance = mock_consumer.return_value
        mock_message = MagicMock()
        mock_message.value.return_value = b"message"
        mock_instance.poll.return_value = mock_message  # Simulating a received message

        consumer = Consumer({"bootstrap.servers": "localhost:9092", "group.id": "test"})
        message = consumer.poll(1.0)  # Mocked poll call

        self.assertEqual(message.value(), b"message")
        mock_instance.poll.assert_called_with(1.0)




