struct Pong {
    1: required double timestamp
}

service Ping {
    Pong ping(1: string name);
}
