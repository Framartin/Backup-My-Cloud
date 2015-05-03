% include('header.tpl', page='List of services', bar_list_services = bar_list_services)
<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
  <div class="list-group">
    <a href="#" class="list-group-item active">
      List of registred services
    </a>
    {{ !list_services }}
  </div>
</div>

% include('foother.tpl')
