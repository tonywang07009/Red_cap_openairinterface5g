% ulsim command for same pusch config
% ./nr_ulsim -m 27 -u 1 -R 51 -r 51 -s 300 -o uci_on_pusch_7.bin

carrier = nrCarrierConfig;
carrier.NSizeGrid = 51;
carrier.NSlot = 8;
carrier.SubcarrierSpacing = 30;
carrier.CyclicPrefix = "normal";

pusch = nrPUSCHConfig;
pusch.PRBSet = 0:carrier.NSizeGrid-1;
pusch.SymbolAllocation = [0,12];
pusch.MappingType = "B";
pusch.NID = 0;
pusch.RNTI = 4660;
pusch.NumLayers = 1;
pusch.TransformPrecoding = false;
pusch.TransmissionScheme = "nonCodebook";
pusch.NumAntennaPorts = 1;
pusch.TPMI = 0;
pusch.Modulation = "64QAM";

pusch.DMRS.DMRSConfigurationType = 1;
pusch.DMRS.DMRSTypeAPosition = 2;
pusch.DMRS.NumCDMGroupsWithoutData = 1;
pusch.DMRS.DMRSAdditionalPosition = 0;
pusch.DMRS.NIDNSCID = 0;
pusch.DMRS.NRSID = 0;
pusch.DMRS.NSCID = 0;
pusch.DMRS.GroupHopping = 0;
pusch.DMRS.SequenceHopping = 0;

pusch.BetaOffsetACK = 20;
pusch.BetaOffsetCSI1 = 6.25;
pusch.BetaOffsetCSI2 = 1;
pusch.UCIScaling = 1;

A = 37896;
rate = 910 / 1024;
rv = 0;
modulation = pusch.Modulation;
nlayers = pusch.NumLayers; % Number of layers for decoding

oack = 7;
ocsi1 = 0;
ocsi2 = 0;
cbsInfo = nrULSCHInfo(pusch, rate, A, oack, ocsi1, ocsi2); % Get ULSCH information

ack = randi([0 1],oack,1);
csi1 = randi([0 1],ocsi1,1);
csi2 = randi([0 1],ocsi2,1);
cack = nrUCIEncode(ack,cbsInfo.GACK,pusch.Modulation);
ccsi1 = [];
ccsi2 = [];

tb_data = randi([0 1],A,1);
% Transport block CRC attachment
tbIn = nrCRCEncode(tb_data,cbsInfo.CRC);

% Code block segmentation and CRC attachment
cbsIn = nrCodeBlockSegmentLDPC(tbIn,cbsInfo.BGN);

% LDPC encoding
enc = nrLDPCEncode(cbsIn,cbsInfo.BGN);

% Rate matching and code block concatenation
chIn = nrRateMatchLDPC(enc,cbsInfo.GULSCH,rv,modulation,nlayers);
culsch = chIn;


% Get the codeword and locations of each type (data and UCI)
[cw,indInfo] = nrULSCHMultiplex(pusch,rate,A,culsch,cack,ccsi1,ccsi2);
cw_scr = nrPUSCHScramble(cw,pusch.NID,pusch.RNTI);

% Write to bin file
fid = fopen('uci_on_pusch_7.bin', 'wb');
to_write = [A,oack,ocsi1,ocsi2,length(cw),length(cw_scr)];
fwrite(fid, to_write, 'uint32'); % Write the data to the binary file
fwrite(fid, tb_data, "uint8");
fwrite(fid, ack, "uint8");
fwrite(fid, csi1, "uint8");
fwrite(fid, csi2, "uint8");
fwrite(fid, cw, "uint8");
fwrite(fid, cw_scr, "uint8");
fclose(fid); % Close the file after writing
