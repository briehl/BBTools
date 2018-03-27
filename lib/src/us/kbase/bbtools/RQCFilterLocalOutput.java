
package us.kbase.bbtools;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: RQCFilterLocalOutput</p>
 * <pre>
 * The output from the local function version of RQCFilter.
 * output_directory:
 *     the path to the output directory containing all files generated by RQCFilter.
 * run_log:
 *     the path to the run log from RQCFilter (i.e. its stderr). This will be a path in the
 *     output directory, added separately here for convenience.
 * filtered_fastq_file:
 *     the path to the file (in the output directory) containing the filtered FASTQ reads.
 *     This will likely be compressed, if you need it decompressed, you can use
 *     DataFileUtil.unpack_file (see that module).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "output_directory",
    "run_log",
    "filtered_fastq_file"
})
public class RQCFilterLocalOutput {

    @JsonProperty("output_directory")
    private String outputDirectory;
    @JsonProperty("run_log")
    private String runLog;
    @JsonProperty("filtered_fastq_file")
    private String filteredFastqFile;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("output_directory")
    public String getOutputDirectory() {
        return outputDirectory;
    }

    @JsonProperty("output_directory")
    public void setOutputDirectory(String outputDirectory) {
        this.outputDirectory = outputDirectory;
    }

    public RQCFilterLocalOutput withOutputDirectory(String outputDirectory) {
        this.outputDirectory = outputDirectory;
        return this;
    }

    @JsonProperty("run_log")
    public String getRunLog() {
        return runLog;
    }

    @JsonProperty("run_log")
    public void setRunLog(String runLog) {
        this.runLog = runLog;
    }

    public RQCFilterLocalOutput withRunLog(String runLog) {
        this.runLog = runLog;
        return this;
    }

    @JsonProperty("filtered_fastq_file")
    public String getFilteredFastqFile() {
        return filteredFastqFile;
    }

    @JsonProperty("filtered_fastq_file")
    public void setFilteredFastqFile(String filteredFastqFile) {
        this.filteredFastqFile = filteredFastqFile;
    }

    public RQCFilterLocalOutput withFilteredFastqFile(String filteredFastqFile) {
        this.filteredFastqFile = filteredFastqFile;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((("RQCFilterLocalOutput"+" [outputDirectory=")+ outputDirectory)+", runLog=")+ runLog)+", filteredFastqFile=")+ filteredFastqFile)+", additionalProperties=")+ additionalProperties)+"]");
    }

}