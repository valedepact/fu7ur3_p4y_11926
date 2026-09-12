import 'package:intl/intl.dart';

class DateRange {
  final DateTime start;
  final DateTime end;
  DateRange(this.start, this.end);

  String get startIso => DateFormat('yyyy-MM-dd').format(start);
  String get endIso => DateFormat('yyyy-MM-dd').format(end);
}

DateRange rangeForPeriod(String period) {
  final today = DateTime.now();
  final todayDate = DateTime(today.year, today.month, today.day);

  switch (period) {
    case 'today':
      return DateRange(todayDate, todayDate);
    case 'week':
      final start = todayDate.subtract(Duration(days: todayDate.weekday % 7));
      return DateRange(start, todayDate);
    case 'month':
      final start = DateTime(todayDate.year, todayDate.month, 1);
      return DateRange(start, todayDate);
    default:
      return DateRange(todayDate, todayDate);
  }
}