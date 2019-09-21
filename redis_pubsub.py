import redis
from threading import Thread


class SubscriberThread(Thread):
  def __init__(self, channels):
    super().__init__()
    client = redis.Redis(host='redis', port=6379, db=0)
    self.pubsub = client.pubsub()
    self.pubsub.subscribe(channels)

  def run(self):
    for message in self.pubsub.listen():
      print(message)

  def unsubscribe(self):
    # unsubscribeすればlisten止まる
    self.pubsub.unsubscribe()


def main(n_subscribers=2):
  client = redis.Redis(host='redis', port=6379, db=0)
  threads = [SubscriberThread("pubsub") for _ in range(n_subscribers)]

  try:
    for t in threads: t.start()

    # 空文字入力で終了
    s = input()
    while s:
      client.publish("pubsub", s)
      s = input()

  finally:
    for t in threads: t.unsubscribe()
    for t in threads: t.join()


if __name__ == '__main__':
  main()
