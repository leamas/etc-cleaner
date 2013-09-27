#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>

int debug = 1;

static void trace( const char* fmt, ...)
{
    struct timeval now;

    gettimeofday( &now, NULL);
    fprintf( stderr, "%d ", (int) now.tv_usec);
    va_list ap;
    va_start( ap, fmt);
    vfprintf( stderr, fmt, ap);
    va_end( ap);
}


static void daemonize()
{
    pid_t pid;

    pid = fork();
    if( pid == -1){
        perror( "Can't fork!");
        exit( 1);
    }
    else if ( pid > 0)
        _exit( 0);

    // child...
    if (setsid() == (pid_t)-1) {
        fprintf(stderr, "Cannot make setsid (!)\n");
        _exit(1);
    }
}


static int setup_pty(void)
{
    int   fd;
    int   r;
    struct termios tio;

    fd = posix_openpt( O_RDWR | O_NOCTTY);
    //fd = posix_openpt( O_RDWR );
    if( fd == 0){
        perror( "Cannot create pty"); exit( 1);
    };

    r = grantpt( fd);
    if( r != 0){
        perror( "Cannot grant pty"); exit( 1);
    }

    r = unlockpt( fd);
    if( r != 0){
        perror( "Cannot unlock pty"); exit( 1);
    }

    return fd;
}


int main(int argc, char* argv[])
{
    int pty_fd;
    int input, output;

    daemonize();
    pty_fd = setup_pty();
    if (dup2(pty_fd, 0) < 0)
        perror( "Cannot dup2 stdin");
    if (dup2(pty_fd, 1) < 0)
        perror( "Cannot dup2 stdout");
    if (ioctl(pty_fd, TIOCSCTTY, 0) == -1){
        perror("Cannot make TIOCSCTTY");
        _exit(1);
    }
    int tty_fd = open("/dev/tty", O_RDWR|O_NOCTTY);
    if (tty_fd < 0)
	perror("Cannot open /dev/tty");
    system("cat /proc/self/stat");
    system("sudo ls /root");
    system("cat /proc/self/stat");
    system("sudo ls /root");
}
