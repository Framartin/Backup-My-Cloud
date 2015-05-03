% setdefault('page', 'Dashboard')
% setdefault('class_active', ' class="active"')
% setdefault('span_active', ' <span class="sr-only">(current)</span>')
% setdefault('bar_list_services', '')
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="BackupMyCloud - {{ page }}">
    <meta name="author" content="Framartin">
    <link rel="icon" href="./static/favicon.ico">

    <title>BackupMyCloud - {{ page }}</title>

    <!-- Bootstrap core CSS -->
    <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="bootstrap/css/dashboard.css" rel="stylesheet">

    <!-- Framasoft Custom styles -->
    <link href="bootstrap/css/frama.css" rel="stylesheet">

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>

    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/">
            <img alt="BackupMyCloud" src="static/icon.png" style="width: 40px">
          </a>
          <a class="navbar-brand nav nav-pills active" href="/">BackupMyCloud</a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
          <ul class="nav navbar-nav navbar-right">
            <li><a href="/">Dashboard</a></li>
            <li><a href="/settings">Settings</a></li>
            <li><a href="/help">Help</a></li>
            <li><a href="/about">About</a></li>
          </ul>
          <form class="navbar-form navbar-right" action='/search' method='post'>
            <input type="text" class="form-control" placeholder="Search...">
          </form>
        </div>
      </div>
    </nav>

    <div class="container-fluid">
      <div class="row">
        <div class="col-sm-3 col-md-2 sidebar">
          <ul class="nav nav-sidebar">
            <li{{ !class_active if page =='Home' else ''}}><a href="/">Home{{ !span_active if page =='Home' else ''}}</a></li>
            <li{{ !class_active if page =='Settings' else ''}}><a href="/settings">Settings{{ !span_active if page =='Settings' else ''}}</a></li>
            <li{{ !class_active if page =='List of services' else ''}}><a href="/services">List of services{{ !span_active if page =='List of services' else ''}}</a></li>
            <li{{ !class_active if page =='Export' else ''}}><a href="#">Export{{ !span_active if page =='Export' else ''}}</a></li>
          </ul>
          <ul class="nav nav-sidebar">
            {{ !bar_list_services }}
          </ul>
        </div>

