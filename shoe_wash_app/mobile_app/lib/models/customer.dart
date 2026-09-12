class Customer {
  final int id;
  final String name;
  final String? phone;

  Customer({required this.id, required this.name, this.phone});

  factory Customer.fromJson(Map<String, dynamic> json) {
    return Customer(id: json['id'], name: json['name'], phone: json['phone']);
  }
}