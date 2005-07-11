$Id$

zasyncdispatcher is a small product that uses zasync
to provide a load balancer.

Simply create a new Asynchronous Call Dispatcher (ACD) in the zmi
and add some Asynchronous Call Managers (ACM) in it.

the ACD publishes "putCall" and "putSessionCall" that exists in all ACMs

You can call theses methods through ACD like you would
 with a regular ACM, ACD will perform a call on the "less busy"
 ACM.

This is useful only if you are using zasync and want to have more than
 one zasync process running in the background.