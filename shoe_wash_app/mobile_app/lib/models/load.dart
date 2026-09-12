class Load {
  final int id;
  final String droppedOffAt;
  final int customerId;
  final int itemClassId;
  final int quantity;
  final double priceCharged;
  final String status;
  final String? expectedPickupDate;
  final String paymentStatus;

  Load({
    required this.id,
    required this.droppedOffAt,
    required this.customerId,
    required this.itemClassId,
    required this.quantity,
    required this.priceCharged,
    required this.status,
    this.expectedPickupDate,
    required this.paymentStatus,
  });

  double get total => priceCharged * quantity;

  factory Load.fromJson(Map<String, dynamic> json) {
    return Load(
      id: json['id'],
      droppedOffAt: json['dropped_off_at'],
      customerId: json['customer_id'],
      itemClassId: json['item_class_id'],
      quantity: json['quantity'],
      priceCharged: (json['price_charged'] as num).toDouble(),
      status: json['status'],
      expectedPickupDate: json['expected_pickup_date'],
      paymentStatus: json['payment_status'],
    );
  }
}