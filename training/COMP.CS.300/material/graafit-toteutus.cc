




std::unordered_map<int, Node> nodes;

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::vector<Node*> to_neighbours;
};














struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::unordered_set<Node*> to_neighbours;
};











struct Node
{
    // All the data stored in the node
    int id;
    std::string name;
    // ...

    std::vector<Node*> to_neighbours;
    std::vector<Node*> from_neighbours;
};












enum Colour { WHITE, GRAY, BLACK };

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;

    int d; // Distance
    Node* path_back; // π
    Colour colour; // Colour

    std::vector<Node*> to_neighbours;
};













enum Colour { WHITE, GRAY, BLACK };

struct SearchInfo
{
    int d; // Distance
    Node* path_back; // π
    Colour colour; // Colour
};

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;

    SearchInfo* search_info; // Must be created!

    std::vector<Node*> to_neighbours;
};















enum Colour { WHITE, GRAY, BLACK };

struct SearchInfo
{
    int d; // Distance
    int path_back; // π
    Colour colour; // Colour
};

vector<Node> nodes;
vector<SearchInfo> search_infos;

struct Node
{
    // All the data stored in the node
    int id;
    std::string name;

    std::vector<int> to_neighbours;
};
