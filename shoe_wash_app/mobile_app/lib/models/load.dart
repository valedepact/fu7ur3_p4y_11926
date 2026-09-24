import 'load_item.dart';

class Load {
  final int id;
  final String droppedOffAt;
  final int customerId;
  final List<LoadItem> items;
  final double amountPaid;
  final String status;
  final String? expectedPickupDate;
  final String paymentStatus;
  final String deliveryMethod;
  final String? pickupAddress;
  final String? deliveryAddress;

  Load({
    required this.id, required this.droppedOffAt, required this.customerId, required this.items,
    required this.amountPaid, required this.status, this.expectedPickupDate, required this.paymentStatus,
    required this.deliveryMethod, this.pickupAddress, this.deliveryAddress,
  });

  double get total => items.fold(0, (sum, it) => sum + it.total);
  int get totalQuantity => items.fold(0, (sum, it) => sum + it.quantity);

  factory Load.fromJson(Map<String, dynamic> json) {
    return Load(
      id: json['id'],
      droppedOffAt: json['dropped_off_at'],
      customerId: json['customer_id'],
      items: (json['items'] as List).map((e) => LoadItem.fromJson(e)).toList(),
      amountPaid: (json['amount_paid'] as num).toDouble(),
      status: json['status'],
      expectedPickupDate: json['expected_pickup_date'],
      paymentStatus: json['payment_status'],
      deliveryMethod: json['delivery_method'] ?? 'walk_in',
      pickupAddress: json['pickup_address'],
      deliveryAddress: json['delivery_address'],
    );
  }
}