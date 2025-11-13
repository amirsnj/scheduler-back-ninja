import time
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class QueryLoggerMiddleware(MiddlewareMixin):
    
    def process_requests(self, reqeust):
        self.start_time = time.perf_counter()
        connection.queries_log = []


    def process_response(self, request, response):
        duration = (time.perf_counter() - getattr(self, "start_time", 0)) * 1000
        num_queries = len(connection.queries)

        print("\n" + "=" * 80)
        print(f"[{request.method}] {request.path}")
        print(f"⏱  Total time: {duration:.2f} ms | 💾 Queries: {num_queries}")

        total_db_time = 0
        for i, query in enumerate(connection.queries, start=1):
            sql = query["sql"]
            time_taken = float(query["time"]) * 1000
            total_db_time += time_taken
            print(f"  {i:02d}. ({time_taken:.2f} ms) {sql}")

        print(f"🔹 DB total time: {total_db_time:.2f} ms\n")
        print("=" * 80 + "\n")

        return response