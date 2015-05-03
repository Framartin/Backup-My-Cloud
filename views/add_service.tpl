% include('header.tpl', page='Settings', bar_list_services = bar_list_services)
<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
  <div class="list-group">
    <h1 class="page-header">Add a new service</h1>
{{ !message }}
<form class="form-horizontal" method="post">
  <div class="form-group">
    <label for="service_name" class="col-sm-2 control-label">Service name</label>
    <div class="col-sm-10">
      <input type="text" class="form-control" id="service_name" name="service_name" placeholder="MyService">
    </div>
  </div>
  <div class="form-group">
    <label for="service_url" class="col-sm-2 control-label">URL</label>
    <div class="col-sm-10">
      <input type="text" class="form-control" id="service_url" name="service_url" placeholder="example.com">
    </div>
  </div>
  <div class="form-group">
    <div class="col-sm-offset-2 col-sm-10">
      <div class="radio">
        <label>
          <input type="radio" name="software_type" id="etherpad" value="etherpad" checked>
          Etherpad (google docs like)
        </label>
      </div>
      <div class="radio">
        <label>
          <input type="radio" name="software_type" id="framadate" value="framadate">
          Framadate (doodle like)
        </label>
      </div>
      </div>
    </div>
  <div class="form-group">
    <div class="col-sm-offset-2 col-sm-10">
      <button type="submit" class="btn btn-default">Register this service</button>
    </div>
  </div>
</form>
  </div>
</div>

% include('foother.tpl')
