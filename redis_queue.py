import redis
from threading import Thread


class WorkerThread(Thread):
  def __init__(self, key):
    super().__init__()
    # single_connection_clientにTrueをセットすると、RedisClientが使うconnectionが固定される
    # 固定しなくても同じconnectionを返してくる可能性は高いと思う
    self.client = redis.Redis(
        host='redis', port=6379, db=0, single_connection_client=True
    )
    self.client_id = self.client.client_id()
    self.key = key
    self.running = True

  def run(self):
    while self.running:
      message = self.client.blpop(self.key, timeout=30)
      if (message):
        print("{}: {}".format(self.client_id, message))

  def stop(self):
    self.running = False
    # self.clientはconnectionが固定されているので、追加でコマンドを実行できない
    client = redis.Redis(host='redis', port=6379, db=0)
    client.client_unblock(self.client_id)


def main(n_workers=2):
  client = redis.Redis(host='redis', port=6379, db=0)
  threads = [WorkerThread("queue") for _ in range(n_workers)]

  try:
    for t in threads: t.start()
    # 空文字入力で終了
    s = input()
    while s:
      client.rpush("queue", s)
      s = input()
  finally:
    print("waiting for workers stopped")
    for t in threads:
      t.stop()

    for t in threads: t.join()


if __name__ == '__main__':
  main()
