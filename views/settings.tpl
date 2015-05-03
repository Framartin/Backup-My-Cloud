% include('header.tpl', page='Settings', bar_list_services = bar_list_services)
<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
  <div class="list-group">
    <a href="#" class="list-group-item active">
      Configure BackupMyCloud
    </a>
    <a href="/global_settings" class="list-group-item"> <span class="badge">1 <span class="glyphicon glyphicon-cog" aria-hidden="true"></span></span> Configure global settings</a>
    <a href="/add_service" class="list-group-item"> <span class="badge">2 <span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></span> Add a new service</a>
  </div>
</div>

% include('foother.tpl')
