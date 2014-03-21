#include <QtGui>
#include "dialog.h"

Dialog::Dialog(QWidget *parent)
    : QDialog(parent)
{
    QLabel *label = new QLabel(tr("hellow, world"));
    QHBoxLayout *mainLayOut = new QHBoxLayout;
    mainLayOut->addWidget(label);
    setLayout(mainLayOut);
}

Dialog::~Dialog()
{

}
