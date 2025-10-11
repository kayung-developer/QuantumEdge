"""
AuraQuant - FIX Protocol Exchange Adapter
"""
import asyncio
import simplefix
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.core.exchange_adapter import ExchangeAdapterProtocol, ConnectionStatus

from app.schemas.trade import OrderResult, OrderType, OrderRequest


# Import all schemas...

class FixAdapter(ExchangeAdapterProtocol):
    exchange_name: str = "FIXBroker"  # Generic name
    _status: ConnectionStatus = ConnectionStatus.DISCONNECTED

    def __init__(self, host, port, sender_comp_id, target_comp_id, password):
        self.host = host
        self.port = port
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.password = password

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.fix_encoder = simplefix.FixEncoder()
        self.fix_decoder = simplefix.FixDecoder()

        self.msg_seq_num = 1
        self.heartbeat_task = None
        self.listener_task = None

        # A dictionary to store pending order statuses, mapping our internal ID to the FIX ClOrdID
        self._pending_orders = {}

    def _create_fix_message(self, msg_type: bytes) -> simplefix.FixMessage:
        """Helper to create a standard FIX message header."""
        msg = simplefix.FixMessage()
        msg.append_pair(8, b"FIX.4.2")  # BeginString
        msg.append_pair(35, msg_type)  # MsgType
        msg.append_pair(49, self.sender_comp_id.encode())  # SenderCompID
        msg.append_pair(56, self.target_comp_id.encode())  # TargetCompID
        msg.append_pair(34, self.msg_seq_num)  # MsgSeqNum
        self.msg_seq_num += 1
        # SendingTime
        msg.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3].encode())
        return msg

    async def _send_message(self, msg: simplefix.FixMessage):
        """Encodes and sends a FIX message to the wire."""
        if not self.writer or self.writer.is_closing():
            raise ConnectionError("FIX connection is not active.")

        buffer = msg.encode()
        self.writer.write(buffer)
        await self.writer.drain()
        print(f"SENT: {buffer.replace(b'x01', b'|')}")

    async def connect(self):
        """Establishes the TCP connection and performs the FIX logon sequence."""
        self._status = ConnectionStatus.CONNECTING
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

            # --- Send Logon Message ---
            logon_msg = self._create_fix_message(b"A")
            logon_msg.append_pair(98, 0)  # EncryptMethod
            logon_msg.append_pair(108, 30)  # HeartBtInt
            logon_msg.append_pair(554, self.password.encode())  # Password
            await self._send_message(logon_msg)

            # --- Wait for Logon Confirmation ---
            # In a real system, the listener task would handle this. We'll simplify here.
            response = await self.reader.read(1024)
            self.fix_decoder.append_buffer(response)
            logon_response = self.fix_decoder.get_message()

            if logon_response and logon_response.get(35) == b"A":
                print("FIX Logon Successful.")
                self._status = ConnectionStatus.CONNECTED
                self.listener_task = asyncio.create_task(self._message_listener())
                self.heartbeat_task = asyncio.create_task(self._heartbeat_sender())
            else:
                raise ConnectionError("FIX Logon failed.")

        except Exception as e:
            self._status = ConnectionStatus.ERROR
            raise ConnectionError(f"FIX connection failed: {e}")

    async def disconnect(self):
        if self.heartbeat_task: self.heartbeat_task.cancel()
        if self.listener_task: self.listener_task.cancel()

        if self.writer and not self.writer.is_closing():
            logout_msg = self._create_fix_message(b"5")
            await self._send_message(logout_msg)
            self.writer.close()
            await self.writer.wait_closed()

        self._status = ConnectionStatus.DISCONNECTED
        print("FIX connection closed.")

    async def _message_listener(self):
        """A background task to continuously read and process incoming FIX messages."""
        while self.get_status() == ConnectionStatus.CONNECTED:
            try:
                data = await self.reader.read(4096)
                if not data: break  # Connection closed by peer

                self.fix_decoder.append_buffer(data)
                while True:
                    msg = self.fix_decoder.get_message()
                    if not msg: break
                    print(f"RECV: {msg.encode().replace(b'x01', b'|')}")
                    # --- Process message based on type (ExecutionReport, etc.) ---
                    # This is where you would update your internal order state.
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in FIX listener: {e}")
                self._status = ConnectionStatus.ERROR
                break

    async def _heartbeat_sender(self):
        """A background task to send heartbeats to keep the session alive."""
        while self.get_status() == ConnectionStatus.CONNECTED:
            await asyncio.sleep(30)
            heartbeat_msg = self._create_fix_message(b"0")
            await self._send_message(heartbeat_msg)

    async def place_order(self, order_request: OrderRequest) -> OrderResult:
        """Sends a NewOrderSingle (D) message."""

        # Generate a unique ID for this order
        cl_ord_id = str(uuid.uuid4())

        msg = self._create_fix_message(b"D")
        msg.append_pair(11, cl_ord_id.encode())  # ClOrdID
        msg.append_pair(55, order_request.symbol.encode())  # Symbol
        msg.append_pair(54, b"1" if order_request.type == OrderType.BUY else b"2")  # Side
        msg.append_pair(38, str(order_request.volume).encode())  # OrderQty
        msg.append_pair(40, b"2")  # OrdType=Limit. A real system would map all types.
        msg.append_pair(44, str(order_request.price).encode())  # Price
        msg.append_pair(59, b"0")  # TimeInForce=Day

        await self._send_message(msg)

        # For FIX, the response is asynchronous. We return a pending result.
        # The listener task will receive the ExecutionReport and update the state.
        return OrderResult(
            retcode=999,  # Custom code for "Pending"
            deal=0,
            order=0,  # The real order ID will come in the ExecutionReport
            volume=order_request.volume,
            price=order_request.price,
            bid=0.0, ask=0.0,
            comment=f"FIX order submitted with ClOrdID {cl_ord_id}",
            request_id=0,
            retcode_message="Pending Execution Report"
        )
