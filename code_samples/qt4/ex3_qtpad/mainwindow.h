#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QtGui>

class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    MainWindow();
protected:
    void closeEvent(QCloseEvent *);

signals:

private slots:
    void newFile();
    void open();
    bool save();
    bool saveAs();
    void windowChanged();

private:
    void createCentralWidget();
    void createActions();
    void createMenus();
    void establishConnections();
    void setCurrentFile(const QString &);
    bool saveFile(const QString &);
    bool loadFile(const QString &);
    bool okToSwitchFile();

private:
    QPlainTextEdit *plainTextEdit;
    QString currentFile;

    QFileDialog *openDiag;
    QFileDialog *saveAsDialog;

    QAction *newFileAction;
    QAction *saveAction;
    QAction *saveAsAction;
    QAction *openAction;
    QAction *quitAction;

    QMenu *fileMenu;
};

#endif // MAINWINDOW_H
