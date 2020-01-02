from pubsub import pub


class SomeReceiver(object):
    def __init__(self):
        pub.subscribe(self.__onObjectAdded, 'object.added')

    def __onObjectAdded(self, data, extra1, extra2=None):
        # no longer need to access data through message.data.
        print(f'Object {repr(data)} is added')
        print(extra1)
        if extra2:
            print(extra2)


a = SomeReceiver()
pub.sendMessage('object.added', data=42, extra1='hello!')
pub.sendMessage('object.added', data=42, extra1='hello!',
                extra2=[2, 3, 5, 7, 11, 13, 17, 19, 23])
