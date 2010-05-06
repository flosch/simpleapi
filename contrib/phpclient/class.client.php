<?php
    /***************************************
     * simpleapi PHP client library v0.1   *
     *                                     *
     * (c) 2010 Florian Schlachter         *
     * http://www.fs-tools.de              *
     * http://github.com/flosch/simpleapi/ *
     ***************************************/

    class ClientException extends Exception {}
    class RemoteException extends ClientException {}
    class ConnectionException extends ClientException {}
    class Client { 
        private $ns, $version, $transport_type, $wrapper_type, $timeout,
                $access_key;

        public function __construct($ns, $access_key=NULL, $version='default',
                                    $transport_type='json', $wrapper_type='default',
                                    $timeout=NULL) {
            $this->ns = $ns;
            $this->access_key = $access_key;
            $this->version = $version;
            $this->transport_type = $transport_type;
            $this->wrapper_type = $wrapper_type;
            $this->timeout = $timeout;
            
            if(!is_null($timeout)) {
                ini_set('default_socket_timeout', $timeout);
            }
        }

        public function __call($name, $args) {
            $params = array(
                '_call' => $name,
                '_output' => $this->transport_type,
                '_input' => $this->transport_type,
                '_wrapper' => $this->wrapper_type,
                '_version' => $this->version,
                '_access_key' => $this->access_key
            );
            
            if (count($args) == 1)
                foreach($args[0] as $key => $value) {
                    if ($this->transport_type == 'json') {
                        $params[$key] = json_encode($value);
                    } else
                        throw new Exception('Unknown transport type.');
                }
            
            try {
                $ch = curl_init();
                curl_setopt($ch, CURLOPT_URL, $this->ns);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
                curl_setopt($ch, CURLOPT_POST, true);
                curl_setopt($ch, CURLOPT_POSTFIELDS, $params);
                $output = curl_exec($ch);
                $info = curl_getinfo($ch);
                curl_close($ch);
            } catch (Exception $e) {
                throw new ConnectionException($e);
            }

            // check http code
            assert($info['http_code'] == 200);

            if ($this->transport_type == 'json') {
                $result = json_decode($output);
                if (!$result->{'success'}) 
                    throw new RemoteException(implode(". ", $result->{'errors'}));
                else
                    return $result->{'result'};
            } else 
                throw new Exception('Unknown transport type.');
        }
    
    }
?>