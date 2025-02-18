struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::vector<Node*> children;
};


std::unordered_map<int, Node> nodes;




struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::vector<std::shared_ptr<Node>> children;
};



struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    Node* left_child; // nullptr if none
    Node* right_child; // nullptr if none
};



struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::vector<Node*> children;
    Node* parent; // nullptr if root
};



struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::unordered_set<Node*> children;
};



std::vector<Node> nodes;

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::vector<int> children;
    int parent; // -1 if root
};
