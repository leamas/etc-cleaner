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

const char* USAGE = ""
"USAGE: attach_term <cmd>\n"
"run <cmd> with stdout attached to a pty.\n"
"\n";



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
    int status;

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


static int setup_pty(char* slave, size_t slavesize)
{
    int   fd;
    int   r;
    struct termios tio;

    fd = posix_openpt( O_RDWR | O_NOCTTY);
    //fd = posix_openpt( O_RDWR );
    if( fd == 0){
        perror( "Cannot create pty"); exit( 1);
	return -1;
    };

    r = grantpt( fd);
    if( r != 0){
        perror( "Cannot grant pty"); exit( 1);
	return -1;
    }

    r = unlockpt( fd);
    if( r != 0){
        perror( "Cannot unlock pty"); exit( 1);
	return -1;
    }
    ptsname_r( fd, slave, slavesize);
    if( slave == NULL){
        perror( "Cannot get pty name"); exit( 1);
	return -1;
    }
    return fd;
}


int main(int argc, char* argv[])
{
    int fd;
    char slave[128];
    int slave_fd;

    if (argc != 2){
        fprintf(stderr, USAGE);
        exit(1);
    }
    daemonize();
    fd = setup_pty( slave, sizeof(slave));
    slave_fd = open(slave, 'r');
    if (slave_fd < 0){
	perror( "Cannot open slave0");
        _exit(1);
    }
    if (dup2(slave_fd, 1) < 0){
        perror( "Cannot dup2 stdout");
        _exit(1);
    }
    system(argv[1]);
    _exit(0);
}
