




std::unordered_map<int, Node> nodes;

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::vector<std::pair<Node*,Cost>> to_neighbours;
};














struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    // ...map, not ..set like before!
    std::unordered_map<Node*,Cost> to_neighbours;
};














struct Edge
{
    int cost;
    string name;
    // ...
};

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    // ...map, not ..set like before!
    std::unordered_map<Node*,Edge> to_neighbours;
};









// In undirected graphs, egde data can be shared between directions
struct Edge
{
    int cost;
    string name;
    Hugedata data;
    // ... too much data or changing data
};

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    // ...map, not ..set like before!
    std::unordered_map<Node*,std::shared_ptr<Edge>> to_neighbours;
};
