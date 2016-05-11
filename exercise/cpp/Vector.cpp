//Vector
using namespace std;

template <typename Object>
class Vector
{
public:
    explicit Vector(int size)
    : size_(size), capacity_(size + SPARE_CAPACITY)
    {
        objects_ = new Object[capacity_];
    }

    virtual ~Vector()
    {
        delete[] objects_;
    }

    Vector(const Vector &rhs)
    : size_(rhs.size_), capacity_(rhs.capacity_)
    {
        objects_ = new Object[capacity_];
        for (int i = 0; i < size_; ++i) {
            objects_[i] = rhs.objects_[i]
        }
    }

    Vector(Vector &&rhs)
    : size_(rhs.size_), capacity_(rhs.capacity_), objects_(rhs.objects_)
    {
        rhs.objects_ = nullptr;
        rhs.size_ = 0;
        rhs.capacity_ = 0;
    }

    Vector & operator= (Vector rhs)
    {
        deepSwap(rhs);
        return *this;
    }

    Vector & operator= (Vector&& rhs)
    {
        lightSwap();
        return *this;
    }

    void deepSwap(Vector &rhs)
    {
        std::swap(*this, rhs);
    }

    void lightSwap(Vector &rhs)
    {
        std::swap(size_, rhs.size_)
        std::swap(capacity, rhs.capacity_)
        std::swap(objects_, rhs.objects_)
    }

    int size() const
    {
        return size_;
    }

    int capacity() const
    {
        return capacity_;
    }

    bool empty() const
    {
        return (size_ == 0);
    }

    void reserve(int newCapacity)
    {
        if (newCapacity < size_) {
            return;
        }

        Object * temp = new Object[newCapacity];
        for (int i = 0; i < size_; ++i) {
            temp[i] = objects_[i];
        }
        capacity_ = newCapacity
        std::swap(temp, objects_);
        delete[] temp;
    }
    void resize(int newSize)
    {
        if (newSize > capacity_) {
            reserve(newSize * 2) // ? why
        }
        size_ = newSize;
    }

    Object & operator[] (int index)
    {
        return objects_[index];
    }

    const Object & operator[] (int index) const
    {
        return objects_[index];
    }

    bool empty() const
    {
        return (size_ == 0) ;
    }

    int size() const
    {
        return size_;
    }

    int capacity() const
    {
        return capacity_;
    }

    void push_back(const Object & x)
    {
        if (size_ == capacity_) {
            reserve(size_ * 2);
        }

        objects_[size_++] = x;
    }

    void push_back(Object &&x)
    {
        if (size_ == capacity_) {
            reserve(size_ * 2);
        }

        objects[size_++] = std::move(x); // call `Object & operator= (Object &&rhs)`
    }

    void pop_back()
    {
        --size_;
    }

    const Object & back() const
    {
        return objects[size_ - 1];
    }

    Object & back()
    {
        return objects[size_ - 1];
    }

    typedef Object * iterator;
    typedef const Object * const_iterator;

    iterator begin()
    {
        return &objects[0];
    }

    const_iterator begin() const
    {
        return &objects[0]
    }

    iterator end()
    {
        return &objects[size_];
    }

    const_iterator end() const
    {
        return &objects[size_];
    }


private:
    int size_;
    int capacity_;
    Object * objects_;
}
//big 5
//Vecotr(int)
//~Vector()
//Vector(const Vector &)
//Vector(Vector &&)
//Vector & operator = (const Vector &)
//Vector & operator = (Vector &&)

//Other methods
//int size()
//void clear()
//bool empty()
//void push_back(const Object & x)
//void pop_back(const Object & x)
//Object & front()
//Object & back()
//
//Object & operator [] (int idx)
//Object & at (int idx)
//size_t capacity()
//void reserve(int newCapacity)
//resize(int)
//reserve(int)
