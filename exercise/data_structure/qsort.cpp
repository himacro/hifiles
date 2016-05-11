#include <iostream>
#include <vector>

using namespace std;

typedef vector<int>::size_type vsize_t;
static void fill_array(vector<int> &);
static void print_array(vector<int> &);

static void quick_sort(vector<int> &);
static vsize_t partition(vector<int> &, vsize_t, vsize_t);
static void quick_sort( vector<int> &, vsize_t, vsize_t);

static void merge_sort(vector<int> &);
static void merge_sort(vector<int> &, vsize_t, vsize_t);

int main()
{
    vector<int> array0;
    fill_array(array0);

    auto array = array0;
    print_array(array);

    quick_sort(array);
    cout << "Quick Sort" << endl;
    print_array(array);

    array = array0;
    merge_sort(array);
    cout << "Merge Sort" << endl;
    print_array(array);

    return 0;
}

static void fill_array(vector<int> &array)
{
    int input = 0;
    while (cin >> input)
        array.push_back(input);

    return; }

static void print_array(vector<int> &array)
{
    for (auto & a : array) {
        cout << a << ' ';
    }
    cout << endl;

    return;
}

void quick_sort(vector<int> &array)
{
    quick_sort(array, 0, array.size() - 1);
    return;
}

static void quick_sort(vector<int> &array, vsize_t begin, vsize_t end)
{
    if (begin == end)
        return;

    vsize_t p = partition(array, begin, end);
    if (p > begin + 1)
        quick_sort(array, begin, p - 1);

    if (p < end - 1)
        quick_sort(array, p + 1, end);

    return;
}

static vsize_t partition(vector<int> &array, vsize_t left, vsize_t right)
{
    auto pivot = left;
    auto i = left + 1, j = left + 1;
    while (i <= right && j <= right)
    {
        for (; i <= right && array[i] < array[pivot]; i++);
        if (i > right) break;

        for(j = max(j, i + 1); j <= right && array[j] >= array[pivot]; j++);
        if (j > right) break;

        swap(array[i++], array[j++]);
    }

    if ((--i) > pivot)
        swap(array[i], array[pivot]);

    return i;
}

// Merge Sort
static void merge_sort(vector<int>& array)
{
    merge_sort(array, 0, array.size() - 1);
}

static void merge_sort(vector<int>& array, vsize_t left, vsize_t right)
{
    auto size = right - left + 1;
    switch (size) {
    case 1:
        return;

    case 2:
        if (array[left] > array[right]) {
            swap(array[left], array[right]);
        }
        return;
    }

    // devide
    vsize_t middle = (left + right) / 2;
    merge_sort(array, left, middle);
    merge_sort(array, middle + 1, right);

    // merge
    vector<int> sorted; //(size);
    vsize_t n = 0;
    auto i = left, j = middle +1;

    while (i <= middle && j <= right)
    {
        if (array[i] < array[j])
            sorted.push_back(move(array[i++]));
        else
            sorted.push_back(move(array[j++]));
    }

    while (i <= middle) {
        sorted.push_back(move(array[i++]));
    }

/*
    // 剩余的右子序列已经在正确的位置上
    while (j <= right) {
        sorted[n++] = array[j++];
    }
*/

/*
    右子序列无剩余时, j = right + 1;
    右子序列有剩余时, j 开始的剩余序列已经在正确的位置;
*/
    for (i = left, n = 0; n < sorted.size();) {
        array[i++] = move(sorted[n++]);
    }

    return;
}
