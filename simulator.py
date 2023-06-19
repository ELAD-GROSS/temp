import sys
import numpy as np


class Event:
    def __init__(self, arrival_time, terminate_time, server, is_processed, service_time=0):
        self.arrival_time = arrival_time
        self.terminate_time = terminate_time
        self.server = server
        self.is_processed = is_processed
        self.service_time = service_time


class LoadBalancer:
    def __init__(self, T, N, prob, lambada, queue_sizes, rates):
        self.T = T
        self.N = N
        self.prob = prob
        self.lambada = lambada
        self.queue_sizes = queue_sizes
        self.rates = rates
        self.got_served = 0
        self.dumped = 0
        self.handled_last_req = 0
        self.tot_waiting_time = 0
        self.tot_serving_time = 0
        self.curr_time = 0
        self.events = []
        self.events_in_servers = [[] for _ in range(self.N)]

    def handle_msg(self):
        server_id = np.random.choice(self.N, p=self.prob)  # selecting server
        if len(self.events_in_servers[server_id]) == self.queue_sizes[server_id] + 1:
            self.dumped += 1
            return

        service_time = np.random.exponential(1 / self.rates[server_id])
        if len(self.events_in_servers[server_id]) == 0:
            new_event = Event(self.curr_time, self.curr_time + service_time, server_id, False, service_time)
        else:
            new_event = Event(self.curr_time, self.events_in_servers[server_id][-1].terminate_time + service_time,
                              server_id, False, service_time)

        self.events.append(new_event)
        self.events_in_servers[server_id].append(new_event)

    def serving_msg(self, event):
        self.events_in_servers[event.server].pop(0)
        self.got_served += 1
        self.tot_waiting_time += event.terminate_time - event.arrival_time - event.service_time
        self.tot_serving_time += event.terminate_time - event.arrival_time
        if len(self.events) == 0:
            self.handled_last_req = self.curr_time

    def get_event_by_termination(self):
        self.events.sort(key=lambda x: x.terminate_time)
        return self.events.pop(0)

    def stats(self):
        return self.got_served, self.dumped, self.handled_last_req, self.tot_waiting_time / self.got_served, \
               self.tot_serving_time / self.got_served

    def simulate_load_balancer(self):
        msg_time = np.random.exponential(1 / self.lambada)
        new_event = Event(msg_time, msg_time, 0, True)
        self.events.append(new_event)

        while self.curr_time < self.T:

            new_event = self.get_event_by_termination()
            self.curr_time = new_event.terminate_time

            if new_event.is_processed:
                msg_time = np.random.exponential(1 / self.lambada)
                new_event = Event(self.curr_time, self.curr_time + msg_time, 0, True)
                self.events.append(new_event)
                self.handle_msg()
            else:
                self.serving_msg(new_event)

        while len(self.events) > 0:
            event = self.get_event_by_termination()
            self.curr_time = event.terminate_time
            self.handle_msg() if event.is_processed else self.serving_msg(event)

        return self.stats()


def main():
    args = sys.argv
    T = int(args[1])
    N = int(args[2])
    prob = args[3:N + 3]
    prob = [float(i) for i in prob]
    lambada = float(args[N + 3])
    queue_sizes = args[N + 4: 2 * N + 4]
    queue_sizes = [float(i) for i in queue_sizes]
    rates = args[2 * N + 4: 3 * N + 4]
    rates = [float(i) for i in rates]
    print(*LoadBalancer(T, N, prob, lambada, queue_sizes, rates).simulate_load_balancer())


if __name__ == '__main__':
    main()