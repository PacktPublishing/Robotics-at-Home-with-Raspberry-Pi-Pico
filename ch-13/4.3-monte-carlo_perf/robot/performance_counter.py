import time


class PerformanceCounter:
    def __init__(self):
        self.count = 0
        self.total_time = 0
        self.start_time = 0
    
    def start(self):
        self.start_time = time.monotonic()
    
    def stop(self):
        end = time.monotonic()
        self.total_time += (end - self.start_time)
        self.count += 1

    def per_call(self):
        return self.total_time / self.count
    
    def total_call_time(self):
        return self.total_time
    
    def call_count(self):
        return self.count
    
    def performance_line(self):
        return f"Calls: {self.count}, Total time: {self.total_time} s, Per call: {self.per_call()}"


# class PerformanceCounterDecorator:
#     def __init__(self, fn):
#         self.count = 0
#         self.total_time = 0
#         self.fn = fn
    
#     def __call__(self, *args, **kwargs):
#         start = time.monotonic()
#         try:
#             print(f"Calling method with {args}, {kwargs}")
#             return self.fn(*args, **kwargs)
#         finally:
#             end = time.monotonic()
#             self.total_time += (end - start)
#             self.count += 1
            
#     def per_call(self):
#         return self.total_time / self.count
    
#     def total_call_time(self):
#         return self.total_time
    
#     def call_count(self):
#         return self.count
    
#     def performance_line(self):
#         return f"Calls: {self.count}, Total time: {self.total_time} s, Per call: {self.per_call()}"


# @PerformanceCounter
# def slow_printer(stuff):
#     print(f"Hello, {stuff}")
#     time.sleep(0.05)
#     return "hello"

# class SomeClass:
#     def __init__(self, stuff):
#         self.stuff = stuff
        
#     @PerformanceCounter
#     def test(self, more_stuff):
#         print(self.stuff, more_stuff)
#         return 5

# result = slow_printer("first_thing")
# print(f"result is {result}")
# # for n in range(1000):
# #    slow_printer("first_thing")
# #    slow_printer("second_thing")
# print(slow_printer.performance_line())

# some_instance = SomeClass("foo")
# result = some_instance.test("bar")
# print(result)
# print(SomeClass.test.performance_line())
