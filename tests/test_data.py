create_order_data = [
    (
        {
            "package_name": "",
            "weight": 10,
            "type_id": 2,
            "cost_content": 1000
        },
        True
    ),
    (
        {
            "package_name": "(*)'':.",
            "weight": 10,
            "type_id": 2,
            "cost_content": 1000
        },
        True
    ),
    (
        {
            "package_name": "12345",
            "weight": 10,
            "type_id": 2,
            "cost_content": 1000
        },
        True
    ),
    (
        {
            "package_name": "PC",
            "weight": "10",
            "type_id": "qqqqq",
            "cost_content": "1000"
        },
        False
    ),
    (
        {
            "package_name": "PC",
            "weight": 10.5,
            "type_id": 2,
            "cost_content": 1000.5
        },
        True
    )
]
