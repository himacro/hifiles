#ifndef REPLACEDIALOG_H
#define REPLACEDIALOG_H

#include <QtGui/QDialog>
#include <QtGui>

class ReplaceDialog : public QDialog
{
    Q_OBJECT

public:
    ReplaceDialog(QWidget *parent = 0);
    ~ReplaceDialog();

public slots:
    void checkToEnableFindButton();
    void checkToEnableReplaceButton();
    void doFind();
    void doReplace();

private:
    QLabel *labelFindWhat;
    QLabel *labelReplaceWith;
    QLineEdit *lineEditFindWhat;
    QLineEdit *lineEditReplaceWith;
    QCheckBox *checkBoxMatchCase;
    QCheckBox *checkBoxReplaceAll;
    QCheckBox *checkBoxFindPrevious;
    QPushButton *pushBtnCancel;
    QPushButton *pushBtnFind;
    QPushButton *pushBtnReplace;
    QTextEdit *textEdit;

private:
    void createWidgets();
    void arrangeLayouts();
    void setTabOrder();
    void establishConnections();
    QTextDocument::FindFlags findFlags();
};

#endif // REPLACEDIALOG_H
