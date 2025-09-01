import time, random, string

def make_id(prefix: str) -> str:
    ts = str(int(time.time()))
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{ts}{rnd}"
