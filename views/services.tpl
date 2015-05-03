% include('header.tpl', page='Services', bar_list_services = bar_list_services)
<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
  <div class="list-group">
    <h1 class="page-header">Backups of {{service}}</h1>
{{ !list_content }}
  </div>
</div>

% include('foother.tpl')
