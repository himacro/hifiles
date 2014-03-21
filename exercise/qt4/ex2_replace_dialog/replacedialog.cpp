#include <QtGui>
#include "replacedialog.h"

ReplaceDialog::ReplaceDialog(QWidget *parent)
    : QDialog(parent)
{
    setWindowTitle(tr("Find and Replace"));
    createWidgets();
    arrangeLayouts();
    setTabOrder();
    establishConnections();
}

ReplaceDialog::~ReplaceDialog()
{

}

void
ReplaceDialog::createWidgets()
{
    labelFindWhat = new QLabel(tr("Find what:"));
    labelReplaceWith = new QLabel(tr("Replace with:"));
    lineEditFindWhat = new QLineEdit;
    lineEditReplaceWith = new QLineEdit;

    checkBoxMatchCase = new QCheckBox(tr("Match case"));
    checkBoxMatchCase->setChecked(false);
    checkBoxReplaceAll = new QCheckBox(tr("Replace all at once"));
    checkBoxFindPrevious = new QCheckBox(tr("Find Previous"));
    checkBoxFindPrevious->setChecked(false);

    pushBtnCancel = new QPushButton(tr("Cancel"));
    pushBtnFind = new QPushButton(tr("Find"));
    pushBtnFind->setEnabled(false);
    pushBtnReplace = new QPushButton(tr("Find and Replace"));
    pushBtnReplace->setEnabled(false);

    textEdit = new QTextEdit;
}

void
ReplaceDialog::arrangeLayouts()
{
    QFormLayout *layoutString = new QFormLayout;
    layoutString->addRow(labelFindWhat, lineEditFindWhat);
    layoutString->addRow(labelReplaceWith, lineEditReplaceWith);

    QVBoxLayout *layoutOptions = new QVBoxLayout;
    layoutOptions->addWidget(checkBoxMatchCase);
    layoutOptions->addWidget(checkBoxFindPrevious);
    layoutOptions->addWidget(checkBoxReplaceAll);

    QVBoxLayout *layoutExecutions = new QVBoxLayout;
    layoutExecutions->addWidget(pushBtnFind);
    layoutExecutions->addWidget(pushBtnReplace);
    layoutExecutions->addWidget(pushBtnCancel);

    QHBoxLayout * layoutMiddle = new QHBoxLayout;
    layoutMiddle->addLayout(layoutOptions);
    layoutMiddle->addStretch();
    layoutMiddle->addLayout(layoutExecutions);

    QVBoxLayout *layoutTop = new QVBoxLayout;
    layoutTop->addLayout(layoutString);
    layoutTop->addLayout(layoutMiddle);
    layoutTop->addWidget(textEdit);

    setLayout(layoutTop);

}

void
ReplaceDialog::setTabOrder()
{
}

void
ReplaceDialog::establishConnections()
{
    connect(pushBtnCancel, SIGNAL(clicked()), this, SLOT(close()));
    connect(lineEditFindWhat, SIGNAL(textChanged(const QString &)), this, SLOT(checkToEnableFindButton()));
    connect(lineEditFindWhat, SIGNAL(textChanged(const QString &)), this, SLOT(checkToEnableReplaceButton()));
    connect(lineEditReplaceWith, SIGNAL(textChanged(const QString &)), this, SLOT(checkToEnableReplaceButton()));
    connect(pushBtnFind, SIGNAL(clicked()), this, SLOT(doFind()));
    connect(pushBtnReplace, SIGNAL(clicked()), this, SLOT(doReplace()));
}

void
ReplaceDialog::checkToEnableFindButton()
{
    if (!lineEditFindWhat->text().isEmpty())
        pushBtnFind->setEnabled(true);
    else
        pushBtnFind->setEnabled(false);
}

void
ReplaceDialog::checkToEnableReplaceButton()
{
    if (!lineEditFindWhat->text().isEmpty() && !lineEditReplaceWith->text().isEmpty())
        pushBtnReplace->setEnabled(true);
    else
        pushBtnReplace->setEnabled(false);
}

void
ReplaceDialog::doFind()
{
    textEdit->find(lineEditFindWhat->text(), findFlags());
}

void
ReplaceDialog::doReplace()
{
    if (textEdit->find(lineEditFindWhat->text(), findFlags())) {
        QTextCursor cursorAtFind = textEdit->textCursor();
        cursorAtFind.insertText(lineEditReplaceWith->text());
    }
}

QTextDocument::FindFlags
ReplaceDialog::findFlags()
{
    QTextDocument::FindFlags findFlags = 0;
    if (checkBoxFindPrevious->isChecked())
        findFlags |= QTextDocument::FindBackward;
    if (checkBoxMatchCase->isChecked())
        findFlags |= QTextDocument::FindCaseSensitively;

    return findFlags;
}
