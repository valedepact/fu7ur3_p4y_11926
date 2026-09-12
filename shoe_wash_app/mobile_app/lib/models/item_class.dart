class ItemClass {
  final int id;
  final String name;
  final double basePrice;

  ItemClass({required this.id, required this.name, required this.basePrice});

  factory ItemClass.fromJson(Map<String, dynamic> json) {
    return ItemClass(
      id: json['id'],
      name: json['name'],
      basePrice: (json['base_price'] as num).toDouble(),
    );
  }
}