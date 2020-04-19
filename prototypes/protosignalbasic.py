import random

from PySide2.QtCore import QObject, Signal, Slot


class Talker(QObject):
    def __init__(self, name):
        super(Talker, self).__init__()
        self.name = name
        self.greetings = ["Hi!", "Hello.", "Hey.", "Greetings.", "Yo."]

    def talk(self, words):
        print(f"{self.name} says, \"{words}\"")

    def emote(self):
        print(f"{self.name} waves hello.")

    def say_hi(self, greeting=None):
        if greeting is None:
            greeting = random.choice(self.greetings)
        self.talk(f"'{greeting} My name is {self.name}'")


class Conversationalist(Talker):
    def __init__(self, name):
        super(Conversationalist, self).__init__(name)
        self.emote()
        self.say_hi()
        self.talk("It's nice to exist.")
        self.opinions = ["bad", "okay", "fine", "great", "exciting", "quite lovely."]

    def greet(self, talker):
        self.say_hi(f"Hello {talker.name}, it's nice to meet you,")
        talker.say_hi(f"It's nice to meet you, {self.name},")

    def prompt(self, topic, talker):
        self.talk(f"I think {topic} is {random.choice(self.opinions)}, what do you think, {talker.name}?")
        talker.respond(topic)

    def respond(self, topic):
        self.talk(f"Well, I think {topic} is {random.choice(self.opinions)}")


class SSTalker(Talker):
    def __init__(self, name):
        super(SSTalker, self).__init__(name)

amy = Conversationalist("Amy")
bob = Conversationalist("Bob")
amy.greet(bob)
amy.prompt("food", bob)
print("\r\n")

