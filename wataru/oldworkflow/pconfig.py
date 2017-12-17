config = {
    'transform': {
        'function': lambda x: x,
        'param': param(hoge = 123, fuga = 876),
    },
    'trainer_factory': {
        'function': func1,
        'param': [
            param(aaa = 123, bbb = 987),
        ]
    }
}
