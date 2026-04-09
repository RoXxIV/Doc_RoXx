#include <string>
#include <vector>
#include <iostream>
#include <algorithm>

// #TASK_STRUCT#BEGIN
struct Task {
    int id;
    std::string title;
    bool done;
};
// #TASK_STRUCT#END

static std::vector<Task> tasks;
static int nextId = 1;

// #TASK_ADD#BEGIN
void addTask(const std::string& title) {
    tasks.push_back({ nextId++, title, false });
    std::cout << "[+] Task added: " << title << "\n";
}
// #TASK_ADD#END

// #TASK_REMOVE#BEGIN
void removeTask(int id) {
    tasks.erase(
        std::remove_if(tasks.begin(), tasks.end(),
            [id](const Task& t) { return t.id == id; }),
        tasks.end()
    );
    std::cout << "[-] Task removed: " << id << "\n";
}
// #TASK_REMOVE#END

// #TASK_LIST#BEGIN
void listTasks() {
    if (tasks.empty()) {
        std::cout << "(no tasks)\n";
        return;
    }
    for (const auto& task : tasks) {
        std::cout << "[" << (task.done ? "x" : " ") << "] "
                  << task.id << " - " << task.title << "\n";
    }
}
// #TASK_LIST#END

// #TASK_MARK_DONE#BEGIN
bool markDone(int id) {
    // #TASK_FIND#BEGIN
    for (auto& task : tasks) {
        if (task.id == id) {
            task.done = true;
            return true;
        }
    }
    return false;
    // #TASK_FIND#END
}
// #TASK_MARK_DONE#END
