//List
template <typename Object>


class List:
{
private:
    struct Node:
    {
        Node * next_;
        Node * prev_;
        Object obj_;

        Node(const Object & obj= Object{},
             Node *p = nullptr,
             Node *n = nullptr)
        : obj_(obj), prev_(p), next_(n) { }

        Node(const Object && obj,
             Node *p = nullptr,
             Node *n = nullptr)
        : obj_(std::move(obj)), prev_(p), next_(n) { }
    };

public:
    class const_iterator
    {}
    class iterator
    {}


//big five
public:
    List()
    List(const List &rhs)
    ~List()
    List & operator= (const List &rhs)
    List(List &&rhs)
    List & operator= (List &&rhs)

    iterator begin();
    const_iterator begin() const;
    iterator end();
    const_iterator end() const;

    int size() const;
    bool empty() const;

    void clear();

    Object& front();
    const Object& front() const;
    Object& back();
    const Object& back() const;

    void push_front(const Object &obj);
    void push_front(Object &&obj);
    void push_back(const Object &obj);
    void push_back(Object &&obj);

    void pop_front();
    void pop_end();

    iterator insert(iterator itr, const Object &obj);
    iterator insert(iterator itr, Object &&obj);

    iterator erase(iterator itr);
    iterator erase(iterator from, iterator to);

private:
    Node *head_;
    Node *tail_;
    int size_;
};
