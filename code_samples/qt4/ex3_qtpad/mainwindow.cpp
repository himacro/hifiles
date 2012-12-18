#include <QtGui>
#include "mainwindow.h"

MainWindow::MainWindow()
{
    createCentralWidget();
    createActions();
    createMenus();
    establishConnections();
}

void
MainWindow::createCentralWidget()
{
    plainTextEdit = new QPlainTextEdit();
    setCentralWidget(plainTextEdit);
}

void
MainWindow::createMenus()
{
    fileMenu = menuBar()->addMenu(tr("&File"));
    fileMenu->addAction(newFileAction);
    fileMenu->addAction(openAction);
    fileMenu->addAction(saveAction);
    fileMenu->addAction(saveAsAction);
    fileMenu->addAction(quitAction);
}

void
MainWindow::establishConnections()
{
    connect(newFileAction, SIGNAL(triggered()), this, SLOT(newFile()));
    connect(openAction, SIGNAL(triggered()), this, SLOT(open()));
    connect(saveAction, SIGNAL(triggered()), this, SLOT(save()));
    connect(saveAsAction, SIGNAL(triggered()), this, SLOT(saveAs()));
    connect(quitAction, SIGNAL(triggered()), this, SLOT(close()));

    connect(plainTextEdit, SIGNAL(textChanged()), this, SLOT(windowChanged()));
}

void
MainWindow::createActions()
{
    newFileAction = new QAction(tr("&New"), this);
    newFileAction->setShortcut(QKeySequence::New);

    openAction = new QAction(tr("&Open"), this);
    openAction->setShortcut(QKeySequence::Open);

    saveAction = new QAction(tr("&Save"), this);
    saveAction->setShortcut(QKeySequence::Save);

    saveAsAction = new QAction(tr("S&ave as"), this);
    saveAsAction->setShortcut(QKeySequence::SaveAs);

    quitAction = new QAction(tr("&Quit"),this);
    quitAction->setShortcut(QKeySequence::Close);
}

void
MainWindow::newFile()
{
    if (okToSwitchFile()) {
        plainTextEdit->clear();
        setCurrentFile("");
    }
}

void MainWindow::open()
{
    if (okToSwitchFile()) {
        QString fileName = QFileDialog::getOpenFileName(this,
                                                        tr("Open Text"), ".",
                                                        tr("Text files (*.txt)"));
        if (!fileName.isEmpty())
            loadFile(fileName);
    }
}

bool MainWindow::save()
{
    if (currentFile.isEmpty())
        return saveAs();
    else
        return saveFile(currentFile);

}


bool MainWindow::saveAs()
{
    QString fileName = QFileDialog::getSaveFileName(this,
                                                    tr("Save QtPad"), ".",
                                                    tr("Text files (*.txt)"));
    if (fileName.isEmpty())
        return false;

    return saveFile(fileName);
}

bool
MainWindow::saveFile(const QString &fileName)
{
    QFile file(fileName);
    if (!file.open(QIODevice::WriteOnly)) {
        QMessageBox::warning(this, tr("QtPad"),
                             tr("Cannot write file %1:\n%2.")
                             .arg(file.fileName())
                             .arg(file.errorString()));
        return false;
    }

    QTextStream out(&file);
    out << plainTextEdit->toPlainText();
    setCurrentFile(fileName);
    setWindowModified(false);
    return true;
}

bool MainWindow::loadFile(const QString &fileName)
{
    QFile file(fileName);
    if (!file.open(QIODevice::ReadWrite)) {
        QMessageBox::warning(this, tr("QtPad"),
                             tr("Cannot open file %1:\n%2.")
                             .arg(file.fileName())
                             .arg(file.errorString()));
        return false;
    }

    //QTextStream in(&file);
    QString fileContent = QTextStream(&file).readAll();
    plainTextEdit->setPlainText(fileContent);
    setCurrentFile(fileName);
    return true;
}

void MainWindow::windowChanged()
{
    setWindowModified(true);
}

bool
MainWindow::okToSwitchFile()
{
    if (isWindowModified()) {
        int userResponse = QMessageBox::warning(
                    this,
                    "QtPad",
                    "Save changed ?",
                    QMessageBox::Yes | QMessageBox::No | QMessageBox::Cancel);
        if (userResponse == QMessageBox::Yes)
            return save();
        else if (userResponse == QMessageBox::Cancel)
            return false;
    }

    return true;
}

void
MainWindow::setCurrentFile(const QString &fileToSetCurrent)
{
   currentFile = fileToSetCurrent;
}


void MainWindow::closeEvent(QCloseEvent *)
{
}



