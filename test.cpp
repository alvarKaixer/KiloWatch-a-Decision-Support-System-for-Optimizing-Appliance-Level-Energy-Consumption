#include <iostream>
#include <queue>
#include <stack>
#include <string>
#include <vector>

using namespace std;

// ================================================
// CONSTANTS
// ================================================

const int MAX_CUSTOMERS = 50;

// ================================================
// STRUCTS
// ================================================

struct Customer {
    string name;
    int priority; // 0 = regular, 1 = ambulance/fire truck, 2 = authority vehicle
};

struct CompareByPriority {
    bool operator()(const Customer& a, const Customer& b) const {
        return a.priority > b.priority;
    }
};

// ================================================
// TYPE ALIASES
// ================================================

using RegularQueue  = queue<Customer>;
using PriorityQueue = priority_queue<Customer, vector<Customer>, CompareByPriority>;
using ServedStack   = stack<Customer>;

// ================================================
// DISPLAY (RECURSIVE)
// ================================================

void displayRegular(RegularQueue q) {
    if (q.empty()) return;
    cout << "  - " << q.front().name << "\n";
    q.pop();
    displayRegular(q);
}

void displayPriority(PriorityQueue pq) {
    if (pq.empty()) return;
    const Customer& c = pq.top();
    cout << "  - " << c.name << " (Priority Level: " << c.priority << ")\n";
    pq.pop();
    displayPriority(pq);
}

// ================================================
// MENU HANDLERS
// ================================================

void addCustomer(RegularQueue& rq, PriorityQueue& pq, int& total) {
    if (total >= MAX_CUSTOMERS) {
        cout << "Queue is FULL (" << MAX_CUSTOMERS << " customers max).\n";
        return;
    }

    string name;
    int type;

    cout << "Enter customer name: ";
    cin >> name;

    cout << "Customer type:\n"
         << "  1. Regular\n"
         << "  2. Priority\n"
         << "Choice: ";
    cin >> type;

    if (type == 1) {
        rq.push({name, 0});
        total++;
        cout << name << " added to the REGULAR queue.\n";

    } else if (type == 2) {
        int level;
        cout << "Priority level:\n"
             << "  1. Ambulance / Fire Truck\n"
             << "  2. Authority Vehicle\n"
             << "Choice: ";
        cin >> level;

        if (level == 1 || level == 2) {
            pq.push({name, level});
            total++;
            cout << name << " added to the PRIORITY queue.\n";
        } else {
            cout << "Invalid priority level.\n";
        }

    } else {
        cout << "Invalid customer type.\n";
    }
}

void distributeFuel(RegularQueue& rq, PriorityQueue& pq, ServedStack& served, int& total) {
    if (!pq.empty()) {
        Customer c = pq.top();
        pq.pop();
        cout << "Now serving PRIORITY customer: " << c.name << "\n";
        served.push(c);
        total--;

    } else if (!rq.empty()) {
        Customer c = rq.front();
        rq.pop();
        cout << "Now serving REGULAR customer: " << c.name << "\n";
        served.push(c);
        total--;

    } else {
        cout << "No customers in queue.\n";
    }
}

void undoLastServe(RegularQueue& rq, PriorityQueue& pq, ServedStack& served, int& total) {
    if (served.empty()) {
        cout << "Nothing to undo.\n";
        return;
    }

    if (total >= MAX_CUSTOMERS) {
        cout << "Cannot undo — queue is full.\n";
        return;
    }

    Customer last = served.top();
    served.pop();

    if (last.priority == 0) {
        rq.push(last);
        cout << last.name << " returned to the REGULAR queue.\n";
    } else {
        pq.push(last);
        cout << last.name << " returned to the PRIORITY queue.\n";
    }

    total++;
}

void displayWaitingList(RegularQueue rq, PriorityQueue pq, int total) {
    cout << "\n--- PRIORITY QUEUE ---\n";
    if (pq.empty())
        cout << "  (empty)\n";
    else
        displayPriority(pq);

    cout << "\n--- REGULAR QUEUE ---\n";
    if (rq.empty())
        cout << "  (empty)\n";
    else
        displayRegular(rq);

    cout << "\nTotal Waiting: " << total << " / " << MAX_CUSTOMERS << "\n";
}

// ================================================
// MAIN
// ================================================

int main() {
    RegularQueue  regularQueue;
    PriorityQueue priorityQueue;
    ServedStack   servedStack;
    int           totalCustomers = 0;
    int           choice;

    do {
        cout << "\n===== GASQUEUE SYSTEM =====\n"
             << "1. Add Customer\n"
             << "2. Distribute Fuel\n"
             << "3. Undo Last Serve\n"
             << "4. Display Waiting List\n"
             << "0. Exit\n"
             << "Choice: ";
        cin >> choice;

        switch (choice) {
            case 1: addCustomer(regularQueue, priorityQueue, totalCustomers);                              break;
            case 2: distributeFuel(regularQueue, priorityQueue, servedStack, totalCustomers);              break;
            case 3: undoLastServe(regularQueue, priorityQueue, servedStack, totalCustomers);               break;
            case 4: displayWaitingList(regularQueue, priorityQueue, totalCustomers);                       break;
            case 0: cout << "System terminated.\n";                                                        break;
            default: cout << "Invalid choice. Please enter 0–4.\n";                                        break;
        }

    } while (choice != 0);

    return 0;
}