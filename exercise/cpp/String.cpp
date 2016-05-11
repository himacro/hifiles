#include <string.h>
#include <vector>
#include <utility>
#include <iostream>

using namespace std;
class String
{
private:
    char * data_;
public:
    String ()
    : data_(new char[1])
    {
        cout << "Default Constructor" << endl;
        data_[0] = '\0';
    }

    String (const char * data)
    : data_(new char[strlen(data) + 1])
    {
        cout << "Constructor by c string" << endl;
        strcpy(data_, data);
    }

    String (const String & rhs)
    : data_(new char[rhs.size() + 1])
    {
        cout << "Copy Constructing" << endl;
        strcpy(data_, rhs.data_);
    }

    // Why not good?
    // String & operator = (const Strong & rhs)
    // {
    //     char * temp = strdup(rhs.data_);
    //     std::swap(temp, data_)
    //     delete[] temp;
    //     return *this;
    // }

    // Old way
    // String & operator = (const Strong & rhs)
    // {
    //     String temp(rhs);
    //     // std::swap(rhs.data_, data_);
    //     swap(temp);
    //     return *this;
    // }

    String (String && rhs)
    : data_(rhs.data_)
    {
        cout << "Move Construtor" << endl;
        rhs.data_ = nullptr;
    }

    ~String()
    {
        cout << "Destructor" << endl;
        delete[] data_;
    }

    String & operator = (String rhs)
    {
        cout << "Copy Assignment" << endl;
        // std::swap(rhs.data_, data_);
        swap(rhs);
        return *this;
    }

    bool operator == (const String & rhs) const
    {
        if (!strcmp(data_, rhs.data_)) {
            return true;
        }
        return false;
    }

    bool operator < (const String && rhs) const
    {
        if (strcmp(data_, rhs.data_) < 0) {
            return true;
        }
        return false;
    }

    char & operator [] (size_t idx)
    {
        return data_[idx];
    }

    String & operator = (String && rhs)
    {
        cout << "Move Assignment" << endl;
        swap(rhs);
        return *this;
    }

    // 返回size_t
    // int size()
    // {
    //     return strlen(data_); // }

    size_t size() const
    {
        return strlen(data_);
    }

    void swap(String &rhs)
    {
        std::swap(data_, rhs.data_);
    }

    void print() const
    {
        cout << data_ << endl;
    }

};

void foo(String x)
{
}

void bar(const String & x)
{
}

String baz()
{
    String ret("world");
    return ret;
}

int main()
{
    String s0("hello");
    String s1("Hello");

    s0.print();
    s1.print();
    if (s0 == s1) {
        cout << "same" << endl;
    }
    else {
        cout << "not same" << endl;
    }

    s1[0] = 'h';
    s0.print();
    s1.print();
    if (s0 == s1) {
        cout << "same" << endl;
    }
    else {
        cout << "not same" << endl;
    }

}

int sub1()
{
    String s0;          //Constructor without parameters
    String s1("hello"); //Constructor with parameters
    String s2(s0);      //Copy Constructor
    String s3 = s1;     //Copy Constructor
    s2 = s1;

    foo(s1);
    bar(s1);
    foo("temporary");
    bar("temporary");
    String s4 = baz();

    std::vector<String> svec;
    svec.push_back(s0);
    svec.push_back(s1);
    svec.push_back(baz());
    svec.push_back("good job");
}
