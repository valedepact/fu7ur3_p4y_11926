import 'package:flutter/material.dart';

import 'services/local_store.dart';
import 'services/data_service.dart';
import 'theme.dart';
import 'screens/home_screen.dart';
import 'screens/loads_screen.dart';
import 'screens/pickup_requests_screen.dart';
import 'screens/more_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LocalStore.init();
  runApp(const ShoeWashApp());
}

class ShoeWashApp extends StatelessWidget {
  const ShoeWashApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'De pact',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: AppColors.primary, scaffoldBackgroundColor: AppColors.bg,
          appBarTheme: const AppBarTheme(backgroundColor: AppColors.primary, foregroundColor: Colors.white)),
      home: const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});
  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  final _dataService = DataService();
  int _index = 0;

  @override
  void initState() {
    super.initState();
    _dataService.init();
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      HomeScreen(dataService: _dataService),
      LoadsScreen(dataService: _dataService),
      PickupRequestsScreen(dataService: _dataService),
      MoreScreen(dataService: _dataService),
    ];
    return Scaffold(
      body: screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.local_laundry_service), label: 'Loads'),
          NavigationDestination(icon: Icon(Icons.local_shipping), label: 'Pickup Requests'),
          NavigationDestination(icon: Icon(Icons.more_horiz), label: 'More'),
        ],
      ),
    );
  }
}