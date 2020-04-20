import random

from PySide2.QtCore import QObject, Signal, Slot


class Talker(QObject):
    def __init__(self, name):
        super(Talker, self).__init__()
        self.name = name
        self.greetings = ["Hi!", "Hello.", "Hey.", "Greetings.", "Yo."]
        self.emote()

    def talk(self, words):
        print(f"{self.name} says, \"{words.capitalize()}\"")

    def emote(self):
        print(f"{self.name} waves hello.")

    def say_hi(self, greeting=None):
        if greeting is None:
            greeting = random.choice(self.greetings)
        self.talk(f"{greeting} My name is {self.name}")


class Conversationalist(Talker):
    def __init__(self, name):
        super(Conversationalist, self).__init__(name)
        self.say_hi()
        self.talk("It's nice to exist.")
        self.opinions = ["bad", "okay", "fine", "great", "exciting", "quite lovely."]
        print("")

    def greet(self, talker):
        self.say_hi(f"Hello {talker.name.capitalize()}, it's nice to meet you,")
        talker.say_hi(f"It's nice to meet you, {self.name},")

    def prompt(self, topic, talker):
        self.talk(f"I think {topic} is {random.choice(self.opinions)}, what do you think, {talker.name}?")
        talker.respond(topic)

    def respond(self, topic):
        self.talk(f"Well, I think {topic} is {random.choice(self.opinions)}")


class Signals(QObject):
    wave = Signal()
    greetings = Signal(str)
    convo = Signal(str)
    bad_response = Signal()


class SSTalker(Talker):
    talk_signal = Signal(str)

    def __init__(self, name, signals):
        self.signals = signals
        self.signals.wave.connect(self._emote)
        super(SSTalker, self).__init__(name)
        self.talk_signal.connect(self.talk)
        self.talk_signal.emit("It's nice to exist.")
        self.say_hi()
        self.signals.convo.connect(self.respond_conversation)
        self.signals.bad_response.connect(self.offended)
        self.opinions = ["bad", "okay", "fine", "great", "exciting", "quite lovely."]
        self.topics = ["food", "existing", "the sky", "the color red"]
        self.is_leaving = False
        print("")

    @Slot()
    def _emote(self):
        # this workaround is to override the emote called during setup
        # one caveat is you have to init the signal in a different class,
        # otherwise you're stuck in a chicken-egg problem where you can't
        # bind the signal because it gets initialized in the same step it's
        # called
        super(SSTalker, self).emote()

    def emote(self):
        self.signals.wave.emit()

    def respond_greet(self, other_name):
        self.talk_signal.emit(f"Hello {other_name.capitalize()},"
                              "it's nice to meet you."
                              f"My name is {self.name}")

    def say_hi(self):
        super(SSTalker, self).say_hi()
        self.signals.greetings.emit(self.name)
        self.signals.greetings.connect(self.respond_greet)

    @Slot()
    def offended(self):
        self.is_leaving = True

    @Slot()
    def make_conversation(self):
        topic = random.choice(self.topics)
        self.talk_signal.emit(f"{topic} is {random.choice(self.opinions)}, "
                              "what do you think?")
        self.is_leaving = False
        self.signals.convo.disconnect(self.respond_conversation)
        self.signals.convo.emit(topic)
        if self.is_leaving:
            self.talk_signal.emit(f"Okay, if you feel that way...")
        else:
            self.talk_signal.emit("I'm glad we all agree!")
            self.signals.convo.connect(self.respond_conversation)
        print("")

    @Slot()
    def respond_conversation(self, topic):
        opinion = random.choice(self.opinions)
        self.talk_signal.emit(f"I think {topic} is {opinion}.")
        if opinion in ["bad"]:
            self.signals.bad_response.emit()


class CountSpeak(QObject):
    def __init__(self, talker):
        super().__init__()
        self.count = 0
        talker.talk_signal.connect(self.increment)

    def increment(self):
        self.count += 1


amy = Conversationalist("Amy")
bob = Conversationalist("Bob")
amy.greet(bob)
amy.prompt("food", bob)
print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~\r\n")

sigs = Signals()
ciel = SSTalker("Ciel", sigs)
ciel_count = CountSpeak(ciel)
dave = SSTalker("Dave", sigs)
echo = SSTalker("Echo", sigs)
feah = SSTalker("Feah", sigs)

ciel.make_conversation()
dave.make_conversation()
echo.make_conversation()
feah.make_conversation()

print(f"Ciel has spoken {ciel_count.count} times.")