from spark.messages import Message
from spark.rooms import Room
from spark.session import Session
from spark.webhooks import Webhook
from spark.people import Person

import unittest
import json

try:
    from apitoken import TOKEN
except ImportError:
    print
    print('To run live tests, please create a apitoken.py file with the following variables filled in:')
    print("""
    TOKEN = '<YOUR API TOKEN>'

    """)

roomname = 'PYTHON SDK TESTING'
URL = 'https://api.ciscospark.com'

MAX_RANDOM_STRING_SIZE = 20

session = Session(URL, TOKEN)


class OfflineRoom(unittest.TestCase):

    testroom = {
                "id": "Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0",
                "title": "Project Unicorn - Sprint 0",
                "sipAddress": "8675309@ciscospark.com",
                "created": "2015-10-18T14:26:16+00:00"
              }

    def test_0001_load_room_from_dict(self):

        obj = Room.from_json(self.testroom)
        self.assertIsInstance(obj, Room)

    def test_0002_load_room_from_str(self):
            data = json.dumps(self.testroom)
            obj = Room.from_json(data)
            self.assertIsInstance(obj, Room)


class Online_01_Room(unittest.TestCase):


    def test_get_all_rooms(self):
        rooms = Room.get(session)
        self.assertIsInstance(rooms, list)
        self.assertTrue(len(rooms) > 1)

    def test_create_test_room(self):
        room = Room()
        room.title = roomname
        resp = room.create(session)
        self.assertTrue(resp.ok)

    def test_send_message_to_room(self):
        room = Room.get(session, name=roomname)
        resp = room.send_message(session, 'this is a str message')
        self.assertTrue(resp.ok)

    def test_get_room_by_name(self):
        room = Room.get(session, name=roomname)
        self.assertIsInstance(room, Room)


class Online_02_People(unittest.TestCase):
    def test_get_self_info(self):
        resp = session.get('/people/me')
        self.assertTrue(resp.ok)

    def test_find_person_by_email(self):
        me = Person.find(session, name='John')
        self.assertIsInstance(me, list)
        self.assertTrue(len(me) > 1)


class Online_03_Messages(unittest.TestCase):

    def test_create_message(self):
        message = Message()
        room = Room.get(session, name=roomname)
        message.text = 'test message from python sdk automated testing'
        room.send_message(session, message)
        resp = session.post(message.url(), message.json())
        self.assertTrue(resp.ok)

    def test_get_messages(self):

        room = Room.get(session, name=roomname)
        msgs = room.get_messages(session)
        print 'get messages from room {}'.format(room.title)
        for msg in msgs:
            print msg.text

    # this is a valid test, but generates too much noise for active development

    # def test_reply_to_message(self):
    #     messages = self.test_get_messages()
    #     for message in messages:
    #         try:
    #             reply = Message()
    #             reply.roomId = message.roomId
    #             reply.text = 'sdk received message {}'.format(message.text)
    #             session.post(reply.get_url(), reply.get_json())
    #
    #         except UnicodeEncodeError:
    #             raise UnicodeEncodeError('Recieved Unicode error posting: {}'.format(reply))


class Online_04_Webook(unittest.TestCase):

    def test_create_webhook(self):
        webhook = Webhook()
        room = Room.get(session, name=roomname)
        webhook.set_targetUrl('http://foo.net/api/v1')
        webhook.set_filter('roomId={}'.format(room.id))
        webhook.set_name('python sdk testing webhook')
        webhook.set_resource('messages')
        webhook.set_event('created')
        resp = webhook.create(session)
        self.assertTrue(resp.ok)


    def test_get_webhooks(self):
        webhooks = Webhook.get(session)
        print webhooks
        self.assertIsInstance(webhooks, list)


class Online_05_TestCleanup(unittest.TestCase):

    def test_cleanup_after_testing(self):

        room = Room.get(session, name=roomname)
        room.delete(session)



if __name__ == '__main__':
    offline = unittest.TestSuite()
    offline.addTest(OfflineRoom)
    online = unittest.TestSuite()
    online.addTest(Online_01_Room)
    online.addTest(Online_02_People)
    online.addTest(Online_03_Messages)
    online.addTest(Online_04_Webook)
    online.addTest(Online_05_TestCleanup)

    full = unittest.TestSuite([online, offline])

    unittest.main(defaultTest='offline')