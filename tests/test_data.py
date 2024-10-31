from app.schemas.schemas import GetPackage

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

mock_get_orders = [
    GetPackage(
        package_name="PC",
        unic_id="unic_id_1",
        weight=10,
        cost_content=1000,
        cost_shipping=1500,
        type_name="electronics",
        created_at="2024-10-31 13:45:23.123456+00:00",
        updated_at=None
    ),
    GetPackage(
        package_name="Dress",
        unic_id="unic_id_2",
        weight=1,
        cost_content=300,
        cost_shipping=320,
        type_name="1",
        created_at="2024-10-31 13:45:23.123456+00:00",
        updated_at=None
    )

]
