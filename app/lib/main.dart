

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  TextEditingController _usernameController = TextEditingController();
  TextEditingController _passwordController = TextEditingController();

  String serverResponse = "";

  Future<void> sendPostRequest() async {
    final url = 'http://127.0.0.1:5000/login';

    try {
      final Map<String, String> data = {
        "username": _usernameController.text.trim(),
        "password": _passwordController.text.trim(),
      };

      final headers = {"Content-Type": "application/json"};
      final response = await http.post(Uri.parse(url), headers: headers, body: jsonEncode(data));

      if (response.statusCode == 200) {
        // success
        final responseData = json.decode(response.body);
        setState(() {
          serverResponse = responseData.toString();
        });

        if (responseData['success']) {
          // Login successful, navigate to the home screen
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => DataSendingPage(),
            ),
          );
        } else {
          // Login failed, show an error message
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: Text('Error'),
              content: Text(responseData['message']),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('OK'),
                ),
              ],
            ),
          );
        }
      } else {
        // failure
        setState(() {
          serverResponse = "request failure";
        });
      }
    } catch (e) {
      // error
      setState(() {
        serverResponse = "error!: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Login Page"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Padding(
              padding: EdgeInsets.all(20.0),
              child: TextField(
                controller: _usernameController,
                decoration: InputDecoration(
                  labelText: 'Username',
                ),
              ),
            ),
            Padding(
              padding: EdgeInsets.all(20.0),
              child: TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Password',
                ),
              ),
            ),
            ElevatedButton(
              onPressed: sendPostRequest,
              child: Text("Login"),
            ),
            SizedBox(height: 20),
            Text("Server Response: $serverResponse"),
          ],
        ),
      ),
    );
  }
}


class DataSendingPage extends StatefulWidget {
  @override
  _DataSendingPageState createState() => _DataSendingPageState();
}

class _DataSendingPageState extends State<DataSendingPage> {
  bool isSendingData = false;
  String receivedData = "";

  Future<void> sendDataLoop() async {
    String url = 'http://127.0.0.1:5000/get';

    while (isSendingData) {

      var response = await http.post(Uri.parse(url), body: {'message': 'get'});
      if (response.statusCode == 200) {
        // Request successful, update the receivedData with the response data
        final responseData = json.decode(response.body);
        setState(() {
          receivedData = "arrive: ${responseData['arrive']}\n"
              "predicted_classes: ${responseData['predicted_classes']}\n"
              "place: ${responseData['place']}";
        });
      } else {
        // Request failed with some status code, do something if needed
        print("Failed to get data. Status Code: ${response.statusCode}");
      }

      await Future.delayed(Duration(seconds: 1)); // Delay 1 second before sending the next request
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Data Sending Page"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                setState(() {
                  isSendingData = true;
                });
                sendDataLoop();
              },
              child: Text("Start Sending Data"),
            ),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  isSendingData = false;
                });
              },
              child: Text("Stop Sending Data"),
            ),
            SizedBox(height: 20),
            Text("Received Data:"),
            Text(receivedData),
          ],
        ),
      ),
    );
  }
}