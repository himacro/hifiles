#include <QtGui/QApplication>
#include "replacedialog.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    ReplaceDialog w;
    w.show();

    return a.exec();
}
