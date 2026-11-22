<div align="center">

```
 ███╗   ██╗ █████╗ ███████╗███████╗███████╗███████╗███████╗██╗██╗   ██╗███╗   ███╗
 ████╗  ██║██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝██║██║   ██║████╗ ████║
 ██╔██╗ ██║███████║█████╗  █████╗  █████╗  ███████╗█████╗  ██║██║   ██║██╔████╔██║
 ██║╚██╗██║██╔══██║██╔══╝  ██╔══╝  ██╔══╝  ╚════██║██╔══╝  ██║██║   ██║██║╚██╔╝██║
 ██║ ╚████║██║  ██║██║     ███████╗███████╗███████║███████╗██║╚██████╔╝██║ ╚═╝ ██║
 ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
```

### less software. more computer.

*I take apps that eat your CPU, RAM and disk for no reason,*
*strip them to the bone, and rebuild them so they cost almost nothing.*

</div>

---

## `$ whoami`

```
name      Nafeesium
mission   debloat everything
method    delete → measure → rebuild smaller
enemy     software that idles at 400 MB
status    still deleting
```

## `$ top` — the problem

Most apps do one small job and bring a whole runtime, a background updater,
three helper processes and a telemetry client along to do it.
Your machine pays for all of it, all day, whether you open the app or not.

## `$ diff before after`

```
 BEFORE  (the usual bloated app)
 CPU   ████████████████░░░░░░░░   idle spin, always awake
 RAM   ██████████████████████░░   hundreds of MB, doing nothing
 DISK  ████████████████████░░░░   hundreds of MB to ship a text box

 AFTER   (my rebuild)
 CPU   █░░░░░░░░░░░░░░░░░░░░░░░   sleeps until you need it
 RAM   ██░░░░░░░░░░░░░░░░░░░░░░   a few MB
 DISK  █░░░░░░░░░░░░░░░░░░░░░░░   a single small binary
```
<!-- bars are illustrative: swap in your real measured numbers -->

## `$ cat rules.txt`

```
1. No background process unless the user asked for one.
2. No framework to draw a button.
3. If it idles, it should cost zero.
4. One small binary beats an installer, a service and a launcher.
5. Measure first. Delete second. Rebuild third.
```

## `$ ls rebuilt/`

| Project | Replaces | Cost now |
|---|---|---|
| [`your-repo`](https://github.com/your-username/your-repo) | the heavy app it replaces | MB RAM · MB disk |
| [`your-repo`](https://github.com/your-username/your-repo) | the heavy app it replaces | MB RAM · MB disk |
| [`your-repo`](https://github.com/your-username/your-repo) | the heavy app it replaces | MB RAM · MB disk |

## `$ contact`

```
github    @your-username
site      https://your-site
```

<div align="center">

```
idle is the goal.
$ _
```

</div>
