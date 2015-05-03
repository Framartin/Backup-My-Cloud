% include('header.tpl', page='Home', bar_list_services = bar_list_services)

% if no_config:

        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
          <h1 class="page-header">Dashboard</h1>

          <div class="jumbotron">
            <h1>Welcome!</h1>
            <p class="lead">Please configure BackupMyCloud before using it to save your data on your hard drive:
            <ul class="list-unstyled">
              <li><span class="badge">1 <span class="glyphicon glyphicon-cog" aria-hidden="true"></span></span> Global settings: frequency of regular backups, etc.</li>
              <li><span class="badge">2 <span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></span> List supported websites where you have data</li>
              <li><span class="badge">3 <span class="glyphicon glyphicon-cloud" aria-hidden="true"></span></span> Choose your content to save</li>
              <li><span class="badge">4 <span class="glyphicon glyphicon-heart-empty" aria-hidden="true"></span></span> Enjoy!</li>
            </ul>
            </p>
            <p><a class="btn btn-lg btn-soutenir btn-block" href="settings" role="button"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span> Configure your settings</a></p>
            </div>

          </div>

% elif no_websites: # no websites configured


        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
          <h1 class="page-header">Dashboard</h1>

          <div class="jumbotron">
            <h1>Welcome!</h1>
            <p class="lead">Please configure BackupMyCloud before using it to save your data on your hard drive:
            <ul class="list-unstyled">
              <li><span class="badge">1 <span class="glyphicon glyphicon-cog" aria-hidden="true"></span></span> <s>Global settings: frequency of regular backups, etc.</s></li>
              <li><span class="badge">2 <span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></span> List supported websites where you have data</li>
              <li><span class="badge">3 <span class="glyphicon glyphicon-cloud" aria-hidden="true"></span></span> Choose your content to save</li>
              <li><span class="badge">4 <span class="glyphicon glyphicon-heart-empty" aria-hidden="true"></span></span> Enjoy!</li>
            </ul>
            </p>
            <p><a class="btn btn-lg btn-soutenir btn-block" href="settings" role="button"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span> Configure your settings</a></p>
            </div>

          </div>

% else: # ready to use


% end

% include('foother.tpl')
